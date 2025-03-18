# Streamlit Example
<br>

Here you can see an example of combining the data access features of the Rhino SDK, along with Streamlit's interactive web application tool to create visualizations customized to your unique Rhino FCP project and datasets.

## Streamlit Description & Setup
Streamlit is an open-source framework used for building interactive web applications with Python. It is designed to be simple and easy to use, allowing developers to create data-centric applications quickly without needing to have experience with web development or front-end technologies like HTML, CSS, or JavaScript.

### Streamlit installation
To install streamlit, follow the instructions on the website, [streamlit.io](https://streamlit.io/#install)
```
pip install streamlit
streamlit hello
```

## Rhino Project Setup
For this example, you must have set up the following:
 * A project on the Rhino FC platform by the name of ``streamlit project``
 * Within that project, load the 5 files listed in [./data](./data/) as datasets

## Running and Deploying a Streamlit Project
To run the project locally, open a command line prompt in this directory, then run
```
streamlit run streamlit-app.py
```
If you wish to deploy to Streamlit's community cloud, you can follow the instructions [here](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy)

## Getting Help
For additional support, please reach out to [support@rhinohealth.com](mailto:support@rhinohealth.com).
