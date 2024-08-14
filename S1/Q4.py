def main():
    lowercase = [chr(c) for c in range(ord('a'), ord('z') + 1)]
    uppercase = [chr(c) for c in range(ord('A'), ord('Z') + 1)]
    digits = [chr(c) for c in range(ord('0'), ord('9') + 1)]
    special_characters = list("~`!@#$%^&*()-_=+[]{}|;:'\",.<>?/\\")

    all_characters = []
    all_characters.extend(lowercase)
    all_characters.extend(uppercase)
    all_characters.extend(digits)
    all_characters.extend(special_characters)

    print("".join(all_characters))
    print(f"Total characters: {len(all_characters)}")

if __name__ == "__main__":
    main()
