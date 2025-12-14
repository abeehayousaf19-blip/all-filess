import bcrypt
 
def hash_password(plain_txt_pass):
    # Encode password to bytes
    Bytes_pass = plain_txt_pass.encode('utf-8')
    # Generate a salt and hash the password
    Salt = bcrypt.gensalt()
    Hash_pass = bcrypt.hashpw(Bytes_pass,Salt)
    # Decode the hash back to a string
    return Hash_pass.decode('utf-8')
 
def verify(plain_txt_pass,hashed_password):
    # Encode both password and stored hash to bytes
    bytes_pass = plain_txt_pass.encode('utf-8')
    bytes_h = hashed_password.encode('utf-8')
    # Bcrypt will compare it with stored hash
    return bcrypt.checkpw(bytes_pass,bytes_h)
 
# Test Code
test_password = 'SecurePassword123'
 
# Test hashing
hashed = hash_password(test_password)
print(f"Original password: {test_password}")
print(f"Hashed password: {hashed}")
print(f"Hash length: {len(hashed)} characters")
 
# Test verification with correct password
is_valid = verify(test_password, hashed)
print(f"\nVerification with correct password: {is_valid}")
 
# Test verification with incorrect password
is_invalid = verify("WrongPassword", hashed)
print(f"Verification with incorrect password: {is_invalid}")
 
# Defining user file
User_data_file = 'users.txt'
 
# Registeration Func.
def register_user(username, password):
    if user_exists(username):
        return False
   
    hashed = hash_password(password)
 
    with open(User_data_file,'a') as file:
        file.write(f'{username},{hashed}\n')
        return True
   
# Check if user is existing
def user_exists(username):
    try:
        with open(User_data_file,'r') as file:
            return any(line.split(',')[0] == username for line in file)
    except FileNotFoundError:
        return False
   
def login_user(username, password):
    try:
        with open(User_data_file,'r') as file:
            for line in file:
                stored_username, stored_hash = line.strip().split(',')
 
                # Check if username matches
                if stored_username == username:
                    if verify(password, stored_hash): #Verify
                        print(f'Welcome,{username}!')
                        return True
                    else:
                        print('ERROR!! Incorrect Password')
                        return False
    except FileNotFoundError:
        print('ERROR: No user registered yet.')
        return False
    print('ERROR: Username not found.')
    return False          
 
# Validate
def validate_user(username):
    if len(username) < 3:
        return(False,'Username must be 3 characters long.')
    if not username.isalnum():
        return(False,'Username must contain only letters and numbers.')
    return (True,'')
 
def validate_pass(password):
    if len(password) < 8:
        return(False,'Password must be 8 character long.')
    if not any(char.isdigit() for char in password):
        return (False,'Password must contain atleast one number.')
    if not any(char.isupper() for char in password):
        return(False,'Password must contain atleast one uppercase letter.')
    return(True,'')
 
# Display Main Menu - Given
def display_menu():
    """Displays the main menu options."""
    print("\n" + "="*50)
    print(" MULTI-DOMAIN INTELLIGENCE PLATFORM")
    print(" Secure Authentication System")
    print("="*50)
    print("\n[1] Register a new user")
    print("[2] Login")
    print("[3] Exit")
    print("-"*50)
 
 
def main():
    """Main program loop."""
    print("\nWelcome to the Week 7 Authentication System!")
 
    while True:
        display_menu()
        choice = input("\nPlease select an option (1-3): ").strip()
 
        # Registration Flow
        if choice == '1':
            print("\n--- USER REGISTRATION ---")
 
            username = input("Enter a username: ").strip()
 
            # Validate username
            is_valid, error_msg = validate_user(username)
            if not is_valid:
                print(f"Error: {error_msg}")
                continue
 
            password = input("Enter a password: ").strip()
 
            # Validate password
            is_valid, error_msg = validate_pass(password)
            if not is_valid:
                print(f"Error: {error_msg}")
                continue
 
            # Confirm password
            password_confirm = input("Confirm password: ").strip()
            if password != password_confirm:
                print("Error: Passwords do not match.")
                continue
 
            # Register the user
            if register_user(username, password):
                print(f"Success: User '{username}' registered successfully!")
            else:
                print(f"Error: Username '{username}' already exists.")
 
        # Login Flow
        elif choice == '2':
            print("\n--- USER LOGIN ---")
 
            username = input("Enter your username: ").strip()
            password = input("Enter your password: ").strip()
 
            # Attempt login
            login_user(username, password)
 
            input("\nPress Enter to return to main menu...")
 
        # Exit Program
        elif choice == '3':
            print("\nThank you for using the authentication system.")
            print("Exiting...")
            break
 
        else:
            print("\nError: Invalid option. Please select 1, 2, or 3.")
 
 
if __name__ == "__main__":
    main()
 