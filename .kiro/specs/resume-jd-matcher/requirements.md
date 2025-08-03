# Requirements Document

## Introduction

The Resume + Job Description Matcher Agent is an AI-powered tool designed to help recruiters, HR professionals, and job seekers by automatically analyzing the compatibility between resumes and job descriptions. The system will provide quantitative matching scores, identify skill gaps, and suggest actionable improvements to optimize resume-to-job fit. This MVP focuses on core matching functionality with a simple CLI interface, targeting high-demand users including recruiters, placement agencies, HR teams at startups, and job seekers.

## Requirements

### Requirement 1

**User Story:** As a recruiter, I want to upload a resume PDF and job description text, so that I can quickly assess candidate fit without manual review.

#### Acceptance Criteria

1. WHEN a user provides a resume PDF file THEN the system SHALL extract and parse the text content accurately
2. WHEN a user provides a job description as text or paste input THEN the system SHALL process and analyze the content
3. WHEN both resume and job description are provided THEN the system SHALL process them within 30 seconds
4. IF the resume PDF is corrupted or unreadable THEN the system SHALL display a clear error message and request a different file

### Requirement 2

**User Story:** As an HR professional, I want to receive a numerical compatibility score between a resume and job description, so that I can prioritize candidates objectively.

#### Acceptance Criteria

1. WHEN the matching analysis is complete THEN the system SHALL provide a score between 0-100%
2. WHEN generating the score THEN the system SHALL consider skills, experience, qualifications, and role requirements
3. WHEN the score is below 30% THEN the system SHALL indicate "Poor Match"
4. WHEN the score is between 30-70% THEN the system SHALL indicate "Moderate Match"
5. WHEN the score is above 70% THEN the system SHALL indicate "Strong Match"

### Requirement 3

**User Story:** As a job seeker, I want to see which skills from the job description match my resume, so that I can understand my strengths for the position.

#### Acceptance Criteria

1. WHEN the analysis is complete THEN the system SHALL display a list of matching skills found in both documents
2. WHEN displaying matching skills THEN the system SHALL categorize them as technical skills, soft skills, or experience areas
3. WHEN no matching skills are found THEN the system SHALL display "No direct skill matches found"
4. WHEN displaying skills THEN the system SHALL show the exact text from both resume and job description

### Requirement 4

**User Story:** As a job seeker, I want to identify skills mentioned in the job description but missing from my resume, so that I can understand what gaps need to be addressed.

#### Acceptance Criteria

1. WHEN the analysis is complete THEN the system SHALL display a list of skills present in the job description but absent from the resume
2. WHEN displaying missing skills THEN the system SHALL prioritize them by importance based on frequency and context in the job description
3. WHEN missing skills are identified THEN the system SHALL categorize them as "Critical", "Important", or "Nice-to-have"
4. IF no missing skills are identified THEN the system SHALL display "All key skills are present in resume"

### Requirement 5

**User Story:** As a job seeker, I want to receive specific suggestions for improving my resume to better match the job description, so that I can increase my chances of getting an interview.

#### Acceptance Criteria

1. WHEN the analysis is complete THEN the system SHALL provide at least 3 actionable improvement suggestions
2. WHEN generating suggestions THEN the system SHALL focus on adding missing skills, improving keyword usage, and enhancing relevant experience descriptions
3. WHEN providing suggestions THEN the system SHALL be specific and include recommended phrases or sections to add
4. WHEN the resume already strongly matches THEN the system SHALL provide optimization suggestions rather than major changes

### Requirement 6

**User Story:** As a user, I want to interact with the system through a simple command-line interface, so that I can quickly process multiple resume-job combinations without complex setup.

#### Acceptance Criteria

1. WHEN starting the application THEN the system SHALL prompt for resume file path and job description input
2. WHEN the user provides inputs THEN the system SHALL validate file existence and content before processing
3. WHEN processing is complete THEN the system SHALL display all results in a clear, formatted output
4. WHEN an error occurs THEN the system SHALL provide helpful error messages and allow retry
5. WHEN the analysis is complete THEN the system SHALL ask if the user wants to process another combination

### Requirement 7

**User Story:** As a developer, I want the system to use the Perplexity API for intelligent matching analysis, so that the results are accurate and contextually aware.

#### Acceptance Criteria

1. WHEN making API calls THEN the system SHALL use the Perplexity API with proper authentication
2. WHEN the API is unavailable THEN the system SHALL display an appropriate error message and graceful failure
3. WHEN API rate limits are reached THEN the system SHALL inform the user and suggest retry timing
4. WHEN processing requests THEN the system SHALL optimize API usage to stay within reasonable cost limits
5. IF API key is missing or invalid THEN the system SHALL provide clear setup instructions

### Requirement 8

**User Story:** As a user, I want the system to handle various resume formats and job description sources, so that I can use it with real-world documents.

#### Acceptance Criteria

1. WHEN a PDF resume is provided THEN the system SHALL extract text using PyMuPDF library
2. WHEN job description is pasted as text THEN the system SHALL accept and process multi-line input
3. WHEN job description is from a website THEN the system SHALL accept copied text content
4. IF resume extraction fails THEN the system SHALL suggest alternative input methods
5. WHEN processing different document formats THEN the system SHALL maintain consistent output quality