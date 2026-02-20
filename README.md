# Auto News Intelligence Dashboard

A Streamlit dashboard for visualizing automotive news intelligence data.

## Features

- 📊 Interactive funnel visualization showing the pipeline flow
- 📰 Live scrolling headlines
- 🗂️ News grid with filtering by date and category
- 📈 Articles by source (bar chart)
- 🥧 Articles by category (donut chart)
- 🎯 Story scatter plot visualization
- 📄 Detailed stories with expandable articles

## Deployment

This app is deployed on Streamlit Community Cloud.

### Deploy Your Own

1. Fork this repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Sign in with GitHub
4. Click "New app"
5. Select your repository, branch, and `app.py`
6. Click "Deploy"

## Local Development

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Data Format

The app expects a `results.json` file in the same directory with the following structure:

```json
{
  "stats": {
    "total_automobile": 197
  },
  "categories": {
    "Category Name": {
      "total_articles": 50,
      "unique_stories": 45,
      "stories": [...]
    }
  }
}
```

## Requirements

- Python 3.8+
- streamlit
- plotly
- pandas
