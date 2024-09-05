FROM quay.io/astronomer/astro-runtime:12.0.0 AS base

ENV AIRFLOW__CORE__TEST_CONNECTION Enabled

