import streamlit as st
import boto3

def save_to_s3(bucket_name, file_name, file_content):
    s3_client = boto3.client('s3')
    try:
        response = s3_client.put_object(
            Body=file_content,
            Bucket=bucket_name,
            Key=file_name
        )
        return True, ""
    except Exception as e:
        return False, str(e)

def main():
    st.title("Upload Text to S3")

    # Input field for text
    text = st.text_area("Enter your text")

    # Input field for file name
    file_name = st.text_input("Enter the file name (e.g., example.txt)")

    # Input field for bucket name
    bucket_name = st.text_input("Enter the S3 bucket name")

    # Submit button
    if st.button("Submit"):
        if text and file_name and bucket_name:
            # Save the text to S3
            success, error = save_to_s3(bucket_name, file_name, text.encode())
            if success:
                st.success("File uploaded successfully!")
            else:
                st.warning(f"Error uploading file: {error}")
        else:
            st.warning("Please enter all the required information.")

if __name__ == '__main__':
    main()
  