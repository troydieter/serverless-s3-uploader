# S3 Uploader API (AWS CDK Deployment)

This project provides a **serverless API** to generate **pre-signed S3 upload URLs** using **AWS Lambda, API Gateway, and S3**.  
It allows **secure file uploads** of any type while enforcing **API key authentication**.

---

## Features
✅ **Secure Signed URL Uploads** (AWS SDK v3)  
✅ **Supports All File Types** (PNG, PDF, MP4, etc.)  
✅ **API Gateway Throttling & API Key Security**  
✅ **Built with AWS CDK (Python)** for easy deployment  

---

## Setup & Deployment

###  Prerequisites
- **AWS CLI Installed** → [Install Guide](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)  
- **AWS CDK Installed** → Run:  
  ```sh
  npm install -g aws-cdk
  ```
- **Python 3.9+ Installed**
- **AWS Credentials Configured**  
  ```sh
  aws configure
  ```

###  Clone the Repo
```sh
git clone https://github.com/YOUR-ORG/s3-uploader-api.git
cd s3-uploader-api
```

### Install Python Dependencies
```sh
python -m venv .venv
source .venv/bin/activate  # (Mac/Linux) or .venv\Scripts\activate (Windows)
pip install -r requirements.txt
```

### Install Lambda Dependencies
```sh
cd s3UploaderFunction
npm install
cd ..
```

### Deploy the CDK Stack
```sh
cdk deploy
```
After deployment, note the **API Gateway URL** and **API Key** from the output.

---

## How to Use the API

### Get a Signed Upload URL
Use **API Gateway** to request a pre-signed URL:  
```sh
curl -H "x-api-key: YOUR_API_KEY" \
     "https://your-api-id.execute-api.us-east-1.amazonaws.com/prod/upload?contentType=image/png"
```
 **Response Example**:
```json
{
  "uploadURL": "https://your-bucket.s3.amazonaws.com/abc12345?AWSAccessKeyId=...",
  "photoFilename": "abc12345"
}
```

---

###  Upload a File Using the Signed URL
Once you receive the `uploadURL`, upload a file using `curl`:
```sh
curl -X PUT -H "Content-Type: image/png" --upload-file test-image.png "UPLOAD_URL_FROM_STEP_1"
```
✅ **If successful, you will not see any output.**  

---

###  Verify the File in S3
Check if the file exists:
```sh
aws s3 ls s3://YOUR_BUCKET_NAME/
```
Or download it:
```sh
aws s3 cp s3://YOUR_BUCKET_NAME/abc12345 downloaded-file.png
```

---

## Debugging & Troubleshooting
| Issue | Solution |
|-------|----------|
| `403 Forbidden` on API Gateway | Ensure API Key is correct and included in the request headers. |
| `403 Forbidden` on S3 Upload | Check IAM permissions for Lambda, ensure correct S3 bucket policy. |
| `500 Internal Server Error` | Check AWS CloudWatch logs for Lambda errors. |

---

## Cleanup
To remove all AWS resources:
```sh
cdk destroy
```