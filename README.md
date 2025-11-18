# Required File Presence Checker

An automated CI/CD validation system that enforces repository standards by checking for required files and logging compliance data to AWS CloudWatch.

## Overview

This project implements a Python-based validation script integrated with GitHub Actions workflows to automatically verify that repositories contain essential files (README.md and .gitignore). The system blocks pull requests that don't meet standards and maintains an audit trail in AWS CloudWatch with separate beta and production environments.

## Features

- **Automated File Validation** - Python script checks for required files on every pull request
- **CI/CD Integration** - GitHub Actions workflows run automatically on PR and merge events
- **Pull Request Blocking** - Non-compliant PRs are blocked from merging
- **CloudWatch Audit Logging** - Successful validations log metadata to AWS CloudWatch
- **Environment Separation** - Separate log groups for beta (PR) and prod (merge) environments
- **Secure Credential Management** - Uses GitHub Secrets for AWS credentials

## Project Structure

```
required-file-presence-checker/
├── .github/
│   └── workflows/
│       ├── on_pull_request.yml     # Beta workflow - triggers on PRs
│       └── on_merge.yml             # Prod workflow - triggers on merges
├── .gitignore                       # Python artifacts excluded
├── README.md                        # Project documentation
├── check_required_files.py          # Core validation logic
└── cloudwatch-logs-policy.json      # IAM policy for CloudWatch access
```

## How It Works

### Validation Script

The Python script (`check_required_files.py`) performs the following:

1. Checks for the presence of required files (README.md and .gitignore)
2. Collects any missing files into a list
3. Prints error messages if files are missing
4. Exits with code 0 (success) or code 1 (failure)

The exit code determines whether GitHub Actions marks the workflow as passed or failed.

### GitHub Actions Workflows

**Beta Workflow** (`on_pull_request.yml`):
- Triggers when a pull request is opened to the main branch
- Runs the validation script
- If validation passes, logs metadata to CloudWatch beta log group
- If validation fails, blocks the PR from being merged

**Production Workflow** (`on_merge.yml`):
- Triggers when code is merged to the main branch
- Runs the same validation script
- If validation passes, logs metadata to CloudWatch prod log group
- Provides production audit trail

### CloudWatch Logging

When validation succeeds, the workflow logs the following metadata to CloudWatch:

- Workflow name
- Repository name
- Commit SHA
- Actor (who triggered the workflow)
- Event type (pull_request or push)
- Git reference
- Status (success)
- Timestamp

## Prerequisites

To use this project, you need:

- GitHub account with repository access
- AWS account with CloudWatch enabled
- AWS CLI installed and configured
- Basic understanding of:
  - Python (loops, functions, exit codes)
  - GitHub Actions (workflows, secrets)
  - AWS IAM (users, policies, permissions)
  - CloudWatch (log groups, log streams)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/required-file-presence-checker.git
cd required-file-presence-checker
```

### 2. Create CloudWatch Log Groups

Create the CloudWatch log groups in AWS:

```bash
# Create beta log group
aws logs create-log-group \
  --log-group-name /github-actions/required-files-checker/beta \
  --region us-east-1

# Create prod log group
aws logs create-log-group \
  --log-group-name /github-actions/required-files-checker/prod \
  --region us-east-1
```

Verify creation:

```bash
aws logs describe-log-groups \
  --log-group-name-prefix /github-actions/required-files-checker \
  --region us-east-1
```

### 3. Create IAM User and Policy

Create a dedicated IAM user for GitHub Actions:

```bash
aws iam create-user --user-name github-actions-cloudwatch
```

Create the IAM policy (already included in `cloudwatch-logs-policy.json`):

```bash
aws iam create-policy \
  --policy-name GitHubActionsCloudWatchLogging \
  --policy-document file://cloudwatch-logs-policy.json
```

Attach the policy to the user (replace `YOUR_ACCOUNT_ID` with your AWS account ID):

```bash
aws iam attach-user-policy \
  --user-name github-actions-cloudwatch \
  --policy-arn arn:aws:iam::YOUR_ACCOUNT_ID:policy/GitHubActionsCloudWatchLogging
```

### 4. Generate Access Keys

Create access keys for the IAM user:

```bash
aws iam create-access-key --user-name github-actions-cloudwatch
```

**Important:** Save the `AccessKeyId` and `SecretAccessKey` from the output. You won't be able to see the secret key again.

### 5. Configure GitHub Secrets

In your GitHub repository:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click **"New repository secret"** and add:

| Secret Name | Value |
|-------------|-------|
| `AWS_ACCESS_KEY_ID` | Your IAM user access key |
| `AWS_SECRET_ACCESS_KEY` | Your IAM user secret key |
| `AWS_REGION` | `us-east-1` (or your preferred region) |

### 6. Test the System

Create a pull request to test the beta workflow:

```bash
git checkout -b test/validation
git add .
git commit -m "Test: Validate workflow"
git push -u origin test/validation
```

Go to GitHub and create a PR from your test branch to main. The workflow will run automatically.

## Testing Locally

Test the Python script before pushing:

```bash
# Test with files present
python3 check_required_files.py
echo $?  # Should return 0

# Test with missing file (simulate failure)
mv .gitignore .gitignore.backup
python3 check_required_files.py
# Should print error and return 1

# Restore file
mv .gitignore.backup .gitignore
```

## Viewing CloudWatch Logs

### Using AWS CLI

Check beta logs:

```bash
# List recent log streams
aws logs describe-log-streams \
  --log-group-name /github-actions/required-files-checker/beta \
  --order-by LastEventTime \
  --descending \
  --max-items 5

# View log events (replace LOG_STREAM_NAME with actual timestamp)
aws logs get-log-events \
  --log-group-name /github-actions/required-files-checker/beta \
  --log-stream-name "2025-11-16_14-30-45" \
  --limit 10
```

Check prod logs:

```bash
aws logs describe-log-streams \
  --log-group-name /github-actions/required-files-checker/prod \
  --order-by LastEventTime \
  --descending \
  --max-items 5
```

### Using AWS Console

1. Go to AWS CloudWatch console
2. Navigate to **Logs** → **Log groups**
3. Click on `/github-actions/required-files-checker/beta` or `/prod`
4. Click on the most recent log stream
5. View the JSON audit data

## Troubleshooting

### Workflow Fails at "Run required files check"

**Problem:** Required files are missing from the repository.

**Solution:** Ensure README.md and .gitignore exist in the repository root.

### Workflow Fails at "Configure AWS credentials"

**Problem:** GitHub Secrets are not configured or credentials are invalid.

**Solution:** 
- Verify secrets are set in GitHub repository settings
- Check that IAM user credentials are correct
- Ensure AWS access keys are active

### Workflow Fails at "Create CloudWatch log stream"

**Problem:** CloudWatch log group doesn't exist or timestamp format is invalid.

**Solution:**
- Verify log groups exist in AWS
- Check that log stream name doesn't contain colons (uses `YYYY-MM-DD_HH-MM-SS` format)

### Workflow Fails at "Send audit log to CloudWatch"

**Problem:** IAM permissions are insufficient or JSON formatting is incorrect.

**Solution:**
- Verify IAM policy allows `logs:CreateLogStream` and `logs:PutLogEvents`
- Check that the IAM policy is attached to the correct user
- Verify the `--log-events` parameter uses correct JSON array format

## Security Best Practices

- **Never commit AWS credentials** to the repository
- **Use GitHub Secrets** for all sensitive data
- **Follow least privilege** - IAM policy only grants necessary permissions
- **Scope permissions tightly** - IAM policy only allows access to specific log groups
- **Rotate credentials regularly** - Update IAM access keys periodically
- **Monitor CloudWatch logs** - Review audit logs for unexpected activity

## Customization

### Adding More Required Files

Edit `check_required_files.py` and update the `required_files` list:

```python
required_files = [
    'README.md',
    '.gitignore'
]
```

### Changing Log Group Names

Update both workflow files:

1. Change `--log-group-name` in the "Create CloudWatch log stream" step
2. Change `--log-group-name` in the "Send audit log to CloudWatch" step
3. Update CloudWatch log groups in AWS to match

### Modifying Workflow Triggers

Edit `.github/workflows/on_pull_request.yml` to change when the workflow runs:

```yaml
on:
  pull_request:
    branches:
      - main
      - develop  # Add more branches
```

## Technologies Used

- **Python 3.11** - Validation script language
- **GitHub Actions** - CI/CD automation platform
- **AWS CloudWatch** - Centralized logging and monitoring
- **AWS IAM** - Identity and access management
- **Git** - Version control

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Author

**Larry** - IT Professional transitioning to DevOps
- GitHub: [@wrijlarr1431](https://github.com/wrijlarr1431)

## Acknowledgments

- Python training program for foundational scripting skills
- AWS documentation for CloudWatch Logs API reference
- GitHub Actions documentation for workflow best practices