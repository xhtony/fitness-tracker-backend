def update_test_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Replace the import
    content = content.replace(
        'from rest_framework.authtoken.models import Token',
        'from rest_framework_simplejwt.tokens import RefreshToken'
    )
    
    # Replace token creation and client setup
    content = content.replace(
        '        # Create a token for the user\n        self.token = Token.objects.create(user=self.user)\n        \n        # Set up the client with authentication\n        self.client = APIClient()\n        self.client.credentials(HTTP_AUTHORIZATION=\'Token {self.token.key}\')',
        '        # Generate JWT token for the user\n        refresh = RefreshToken.for_user(self.user)\n        self.access_token = str(refresh.access_token)\n        \n        # Set up the client with JWT authentication\n        self.client = APIClient()\n        self.client.credentials(HTTP_AUTHORIZATION=f\'Bearer {self.access_token}\')'
    )
    
    # Save the updated content back to the file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        update_test_file(sys.argv[1])
    else:
        print("Please provide the path to the test file to update.")
