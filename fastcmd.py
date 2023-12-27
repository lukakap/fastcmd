#!/usr/bin/env python3

import argparse
import shlex
import os
from openai import OpenAI
import json
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import subprocess

FILE_NAME = "fastcmd-commands.json"

def parse_command(user_input):
    parser = argparse.ArgumentParser(description='FastCmd - Command Line Tool')
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Subparser for 'add' command
    parser_add = subparsers.add_parser('add', help='Add a new command')
    parser_add.add_argument('-d', '--description', required=True, help='Description of the command')
    parser_add.add_argument('-c', '--commandrun', required=True, help='The command to run')

    # Subparser for 'run' command
    parser_run = subparsers.add_parser('run', help='Run a command')
    parser_run.add_argument('-d', '--description', required=True, help='Description of the command')

    # Subparser for 'openaikey' command
    parser_run = subparsers.add_parser('key', help="Add or See OpenAI Key")
    parser_run.add_argument('-a', '--add', required=False, help="ADD YOUR OPENAI KEY")
    parser_run.add_argument('-s', '--see', required=False, help="SEE YOUR OPENAI KEY")

    return parser.parse_args(shlex.split(user_input))

def generate_embeddings(descriptions):
    client = OpenAI()
    response = client.embeddings.create(
        input=descriptions,
        model="text-embedding-ada-002"  # Example model
    )
    return response.data

def find_closest_match(user_input_embedding, command_embeddings, command_descriptions):
    user_input_embedding = np.array(user_input_embedding.embedding).reshape(1, -1)
    max_similarity = 0
    closest_match = None

    for command, embedding in zip(command_descriptions, command_embeddings):
        command_embedding = np.array(embedding.embedding).reshape(1, -1)
        similarity = cosine_similarity(user_input_embedding, command_embedding)[0][0]
        
        if similarity > max_similarity:
            max_similarity = similarity
            closest_match = command

    return closest_match

def find_matching_description(user_input, saved_descriptions):
    # openai.api_key = os.getenv("OPENAI_API_KEY")

    conversation = [
        {"role": "system", "content": """You are a helpful assistant. Match the user's input with the most relevant saved command description.
         you should return one from assistant saved description, you should return exactly that description that is similiar to user content.
          Example: 
    Saved Descriptions: 
    - Back up the database
    - Update the server
    - Clean temporary files
    Assume the user says, 'I need to make a copy of my database for safety.' You should return 'Back up the database' as it is the closest match. Now, find the best match for the following user input based on the saved descriptions"""},
    ]

    # Add saved descriptions to the conversation
    for desc in saved_descriptions:
        conversation.append({"role": "assistant", "content": f"Description: {desc}"})

    # Add user input
    conversation.append({"role": "user", "content": user_input})
    client = OpenAI()
    # Call the OpenAI API
    response = client.chat.completions.create(
        model="text-davinci-004",  # Specify GPT-4 model
        messages=conversation
    )

    # Extract the response
    return response.choices[0].message.content.strip()

def save_command(description, command):
    try:
        with open(FILE_NAME, 'r+') as file:
            data = json.load(file)
            data[description] = command
            file.seek(0)
            json.dump(data, file, indent=4)
    except FileNotFoundError:
        with open(FILE_NAME, 'w') as file:
            json.dump({description: command}, file, indent=4)

def load_commands():
    try:
        with open(FILE_NAME, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout.decode('utf-8')
    except subprocess.CalledProcessError as e:
        return e.stderr.decode('utf-8')

def main():
    is_openai_key_added = False
    openai_key = None

    while True:
        user_input = input("fastcmd> ")
        if user_input.lower() in ["exit", "quit"]:
            break

        try:
            args = parse_command(user_input)
        except SystemExit:
            # Handle parsing error
            continue
        
        if args.command == "key":
            if args.add != None:
                is_openai_key_added = True
                openai_key = args.add
                os.environ["OPENAI_API_KEY"] = openai_key
                print(f"You Have Added OPENAI Key: {openai_key} ")

            elif args.see != None and is_openai_key_added:
                print(f"YOU OPENAI KEY IS : {args.see}")

        if not is_openai_key_added:
            continue

        if args.command == "add":
            # command_store[args.description] = args.commandrun
            save_command(args.description, args.commandrun)
            print(f"Command added: {args.description}")
        
        elif args.command == "run":
            commands = load_commands()
            command_descriptions = list(commands.keys())

            if len(command_descriptions) == 0:
                print(f"fastcmd> THERE IS NO COMMANDS, PLEASE ADD AT FIRST!")
                continue

            command_embeddings = generate_embeddings(command_descriptions)
            user_input_embedding = generate_embeddings([args.description])[0]
            closest_match = find_closest_match(user_input_embedding, command_embeddings, command_descriptions)
            command_to_run = commands.get(closest_match)
            if command_to_run:
                print(f"fastcmd> FOUND COMMAND - {command_to_run} - DO YOU WANT TO RUN?")
                while True:
                    user_input_to_run = input("fastcmd> ").lower()
                    if user_input_to_run == "yes":
                        print(f"fastcmd> RUN OR GET COMMAND?")
                        while True:
                            user_input_to_run_or_get = input("fastcmd> ").lower()
                            if user_input_to_run_or_get == "run":
                                print(f"fastcmd> Running command: {command_to_run}")
                                print(run_command(command=command_to_run))
                                break
                            elif user_input_to_run_or_get == "get":
                                print(f"fastcmd> COMMAND - {command_to_run}")
                                break
                            else:
                                print(f"fastcmd> Please write down RUN or GET")
                        break
                    elif user_input_to_run == "no":
                        break
                    else:
                        print("fastcmd> Please Type yes OR no")
            else:
                print("Command not found.")

if __name__ == '__main__':
    main()
