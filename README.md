# resume-matcher
AI-based tool that ranks resumes based on how closely it matches to a job description. Useful for HR teams trying to automate filtering of candidate resumes.
# how-to-use
1. Make sure Python is downloaded and properly installed.
2. If it's your first time using this tool, make sure to run the `setup_packages.bat` script by double clicking it (the .bat file can oonly be run on Windows). This would download and install the necessary python packages to use the tool.
3. Place your resume pdf's in the `resumes` folder. There's no limit to the amount of resumes you want to put in.
4. Place the job description text for the job in `job_desc.txt` file.
5. Run the `run_script.bat` file to run the resume-matcher script by double-clicking it. The first time running this script will require an internet connection since it needs to download the AI model. Once the script is done running, it will create an excel file containing the resume names with their corresponding match scores. The higher the match score, the more the resume closely matches the job description.
