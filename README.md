# Web App - Books Available in SG Libraries (NLB)
This is the repository for a side project, [SGLibReads](https://sg-nlb-available-books.onrender.com/), which is a free web app for Singapore residents to search, save and more easily view the availability of Singapore library books. If you are a heavy user of the Singapore libraries, consider giving this web app a try.

## Tell Me Why?
### Why One - Providing a better way to search for NLB books
As of 2023, both the Singapore National Library Board’s (NLB) app and website are great and functional. However, I found it difficult to save and search for book availability on their app and website. Wanting an easier way to hunt down the library books, I hacked out a rudimentary technical solution for my own personal use. As the stars started to align and I learned more technical skills, thanks to NLB and the NLB Udemy Biz account no less, I realised I could develop a solution for the general Singapore public too. I hope to create value for the Singapore public, using skills I learned from public funds.

### Why Two - Changing SG government tech culture
When I learned about the [NLB public APIs](https://www.nlb.gov.sg/main/partner-us/contribute-and-create-with-us/NLBLabs), I realise I could use it for this side project. Unfortunately, the NLB API has so far provided a rather subpar developer experience (see my review [here](https://medium.com/@cliffy-gardens/how-good-is-our-latest-singapore-library-apis-an-honest-review-c32b03e8299b)). Nonetheless, I do feel this is also a chance to start more conversations on how some of our government agencies are running their tech deployments. I know there are competent government agencies running excellent tech solutions for Singapore too, and I hope this side project can do its part to contribute to the further strengthening of the Singapore technical core. Those interested in this conversation can follow me on [Medium](https://medium.com/@cliffy-gardens), or add me on [Linkedin](https://www.linkedin.com/in/cliff-chew-kt/). 

### Why Three - Adding more technical skills
This side project is also a way for me to continue to learn and apply more technical skills into a reasonably real-world setting. Some of the possible features I hope to learn and include into this web app includes:
1. Availability of eBooks
2. Linking to NLB Events from EventBrite 
3. Recommending books

## Getting Started
The following section details the step it takes to start-up a local Supabase and FastAPI server for development purpose.

### Prerequisite: Supabase CLI
The [Supabase CLI](https://supabase.io/docs/guides/cli) is required to manage the database schema and seed data. Please follow the instructions below:

1. Install Supabase CLI using the official guide in your local machine [here](https://supabase.com/docs/guides/cli/getting-started#installing-the-supabase-cli).


2. Authenticate Supabase CLI with the following command:
```bash
supabase login
```

3. Run supabase start to take note of the local Supabase URL and API Key. 
```bash
supabase start
```

4. Copy and Update the `.env` file with the Supabase API Key before beginning of any development.

### FastAPI Server
1. Create and activate virtual environment with `venv`.

    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

2. Install dependencies with pip.

    ```bash
    pip install -r requirements.txt
    ```

3. Update `.env` file with APIKeys from `.env.example` template.

    ```bash
    cp .env.example .env
    ```

4. Start-up FastAPI server with Uvicorn and hot-reloading for development purpose.

    ```bash
    uvicorn src.main:app --reload
    ```

### Code Linting and Formating

This project uses [ruff](https://github.com/astral-sh/ruff) as Python code linter and formatter.

To integrate this seamlessly to your development workflow, we recommend using [pre-commit](https://pre-commit.com/) to run the formatter and linter before commiting to the repo.

1. run `pre-commit install` to set up the git hook scripts

    ```bash
    $ pre-commit install
    pre-commit installed at .git/hooks/pre-commit
    ```

2. run `git commit` as usual to commit your changes.
