# Testing Pillar & Post

![The Landing Page](docs-images/landing_page.png)

## Testing Objectives Against User Stories

I have tried to test all the parts of the website that are fundamental to data privacy or functioning through automated testing. I have used manual testing to test the aesthetic touches.

| ID | User Story | Outcome | Feature(s) | Tested |
|----|------------|---------|------------|--------|
| US1 | As a recruiter launching a new agency, I want to choose from professional templates so that I can quickly create a credible website which fits my client's industry. | Fast website launch without design skills. | 3 selectable templates | Tested by test_pages_load.py |
| US2 | As a recruiter, I want to customise colours so that my website reflects my brand identity. | An individual looking website | Colour picker + contrast checker | Tested Manually |
| US3 | As a recruiter, I want to edit website text and images so that I align with our company ethos | Personalised and credible content. | Text editors + image uploaders | Tested Manually |
| US4 | As a recruiter, I want to upload and edit job adverts easily and quickly. | Accurate and competitive job postings. | Job editor (limit 6) | Tested Manually and in test_firm_data_isolation.py |
| US5 | As a recruiter, I want a dashboard to manage my site and subscription so that I don't need technical knowledge. | An easy to use central dashboard | Tenant dashboard | Tested Manually and in test_dashboard_requires_login.py |
| US6 | As a recruiter, I want secure login tied to my subdomain so that my data remains isolated. | Websites built on separate schemas. | Subdomain routing + authentication | Tested in test_authenticated_user_can_access_own_dashboard.py, test_unauthenticated_request_is_blocked.py and test_sessions_are_scoped_to_tenant_schema.py |
| US7 | As a recruiter, I want candidate applications forwarded via email only so that I minimise GDPR risk. | No candidate data stored in database. | Email forwarding system | Tested in test_emails.py |
| US8 | As a recruiter I want to ensure that my payment details are kept securely. | Secure subscription management. | Stripe integration | Tested in test_checkout_session_redirection.py, test_webhook_payment_success_activates_client.py and test_webhook_payment_failure_deactivates_client.py |
| US9 | As a recruiter, I want a free trial so that I can test the platform before committing. | A good motivator to try, no card needed. | 14-day trial | Tested in test_trial_and_plan.py |
| US10 | As a platform owner, I want tenant data separated at schema level so that cross-tenant data access risk is reduced. | Improved data isolation and compliance posture. | Django Tenants schema separation | Tested in test_firm_data_isolation.py and test_sessions_are_scoped_to_tenant_schema.py |
| US11 | As a recruiter, I want to produce an accessible and usable website with little technical knowledge. | Improved accessibility compliance. | Contrast checker and accessibility testing | Tested Manually |
| US15 | As a returning user, I want to easily locate my login portal so that I can access my site quickly. | Reduced login friction. | Email portal finder | Tested in test_portal_finder.py |

## Manual Testing

### Code Validators

#### HTML Validator

With Django htmls it is easier to enter the urls at the [W3C](https://validator.w3.org/) validator. It has trouble reading the tags if you put the whole files in. 

It gave me 1 warning on the landing page

![html validator heading warning](docs-images/html_warning.png)

I changed the section to a div as advised by the warning.

Everything else passed in the marketing site and the dashboard area.

![html validator pass](docs-images/html_validator.png)

My tenant sites had a small issue, one left over tag and a warning about header orders, caused by using Bootstrap cards and not reordering my headings.

![html validator pass](docs-images/html_tenant_warning.png)

I fixed these issues, then everything passed.


#### CSS VAlidator

I passed all 3 CSS files through the [W3C](https://jigsaw.w3.org/css-validator/validator) validator. There is 1 in the marketing app and 2 in the cms app.

All of them passed with no issues.

![Marketing css validator pass](docs-images/marketing_css_validator.png)


#### Javascript Linter

I used [JSHint](https://jshint.com/) to test all my javascript files. It had some warnings, but they were all to do with using more modern javascript and safe to ignore.

![JSHint warnings](docs-images/jshint.png)


#### Python Standards

I have used Flake8 to help me keep my Python code inline with PEP8 standards.

I have used a few helpers to get my code through, there is a .flake8 file in my base with the following code

# E501 = Line too long
# W291 = Trailing whitespace (end of lines)
# W391 = Blank line at end of file
# F841 = Local variable assigned but never used (e.g. in tests)
ignore = E501, W291, W391, F841
max-line-length = 120
exclude = .git,__pycache__,migrations,venv

This is allowing me longer lines, which I find easier to work with and allowing local variables, which I had in testing and would cause problems if I removed. I did include blank lines at the end of the files and trialing whitespace, but I have gone through the file and fixed all of those errors.


### Features Testing

### Responsiveness

### Accessibility

#### Lighthouse

#### Wave

### User Testing

The first round of user testing found a few bugs. 

- If you had an error during sign up it would fail silently

- If you visited a tenant's live page and tried to open a job advert to see the detail you got a 404 error.

It also uncovered a frustration with the sign up process because you entered your details to create your account, but the login page that followed (while being integral to how the site works because it routes to the subdomain) was annoying because you had to reenter all your details.

All of these were fixed by code improvements.

The second round of user testing went well, with no particular feedback.

## Automated Testing

### Django Testing

I have tried to be as thorough as possible with automated testing, mainly to future proof the site. I ran in to lots of issues with the domain routing which meant that tests were harder to write, but through persistance I am happy with the coverage.

## Test Driven Development

I found this far more challenging with the subdomain environment and found that I was rewriting my tests often through the development process, but I do find this a valuable tool in terms of understanding my code and seeing potential future issues with it. 

A bug that I encountered when testing was persistent database issues - the tests couldn't run because the databases already existed, Django tries to clean the database automatically before each test run if this happens, but I kept being told there was an active user on the database and deleting it was impossible. This turned out to be an issue with having my Neon Postgres DB pooled, which means that it keeps connections open. When I changed it to unpooled this issue was fixed.
 
