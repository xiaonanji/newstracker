import argparse
from database import add_person

def main():
    parser = argparse.ArgumentParser(description="Add a person to the Firebase persons list.")
    parser.add_argument('-n', '--name', type=str, required=True, help="Name of the person to add")
    args = parser.parse_args()
    add_person(args.name)

if __name__ == '__main__':
    main()