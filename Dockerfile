FROM ubuntu:18.04

RUN apt-get update && apt-get install \
    -y --no-install-recommends python3 python3-virtualenv

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m virtualenv --python=/usr/bin/python3 $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies
RUN pip install streamlit
RUN pip install elasticsearch
RUN pip install pandas
RUN pip install sklearn
RUN pip install tqdm
RUN pip install plotnine

# Copy the application:
COPY . /home/customized-recipe/
WORKDIR /home/customized-recipe

# Install trailing dependencies:
RUN pip install -r requirements.txt

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# Uploading data
WORKDIR /home/customized-recipe

EXPOSE 8501
CMD [ "streamlit run", "src/ui2.py" ]