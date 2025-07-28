# Viabili RFQ Analysis

A Streamlit application for analyzing RFQ (Request for Quotation) files by uploading ZIP archives containing blueprints and technical documents.

## Features

- **ZIP Upload**: Upload organized ZIP files containing blueprints and technical documents
- **Real-time Processing**: Monitor task progress with live status updates
- **Google Sheets Integration**: View results directly in embedded Google Sheets
- **Cloud Processing**: Leverages Google Cloud Run API for document analysis

## Local Development

### Prerequisites

- Python 3.8+
- Google Cloud Service Account with appropriate permissions

### Setup

1. Clone the repository:
```bash
git clone https://github.com/sammyboy333/viabiliDepDemo.git
cd viabiliDepDemo
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your Google Service Account credentials:
   - Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`
   - Fill in your actual Google Cloud service account credentials

4. Run the application:
```bash
streamlit run "9_✅_viabili.py"
```

## Deployment to Streamlit Cloud

### Prerequisites

- GitHub repository with your code
- Google Cloud Service Account JSON credentials

### Deployment Steps

1. **Push your code to GitHub** (make sure not to include secrets):
```bash
git add .
git commit -m "Initial deployment setup"
git push origin main
```

2. **Deploy to Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub account
   - Select your repository: `sammyboy333/viabiliDepDemo`
   - Set the main file path: `9_✅_viabili.py`

3. **Configure Secrets in Streamlit Cloud**:
   - In your Streamlit Cloud app dashboard, go to "Settings" → "Secrets"
   - Add your Google Service Account credentials in TOML format:

```toml
[google_service_account]
type = "service_account"
project_id = "your-actual-project-id"
private_key_id = "your-actual-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nYour-Actual-Private-Key-Here\n-----END PRIVATE KEY-----\n"
client_email = "your-actual-service-account@your-project.iam.gserviceaccount.com"
client_id = "your-actual-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/your-actual-service-account%40your-project.iam.gserviceaccount.com"
```

4. **Save and Deploy**: Your app will automatically redeploy with the new secrets.

## Usage

1. **Select Upload Mode**: Choose "Subir ZIP ordenado" (Upload Organized ZIP)
2. **Organize Your Files**: Structure your files as shown in the instructions:
   ```
   📁 MiCarpeta  
   ├── 📁 Item1  
   │   ├── 📄 blueprint1.pdf  
   │   ├── 📄 blueprint2.png  
   ├── 📁 Item2  
   │   ├── 📄 blueprint3.jpg  
   │   ├── 📄 blueprint4.step  
   ```
3. **Upload and Execute**: Upload your ZIP file and click "Ejecutar"
4. **Monitor Progress**: Watch the real-time status updates
5. **View Results**: Results will be displayed in an embedded Google Sheets view

## Security Notes

- Never commit your actual service account credentials to version control
- Use Streamlit Cloud's secrets management for production deployment
- The local `secrets.toml` file is ignored by git for security

## Troubleshooting

- **Authentication Errors**: Verify your Google Cloud service account has the correct permissions
- **Upload Errors**: Ensure your ZIP file follows the required folder structure
- **Deployment Issues**: Check that all secrets are properly configured in Streamlit Cloud

## Support

For issues or questions, please contact the development team or create an issue in the GitHub repository.
