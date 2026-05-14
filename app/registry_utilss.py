"""
Module: registry_utils.py
=====

This module provides utility functions for dynamic model retrieval within the 
Django project ecosystem.

Similar to Django's **get_user_model()**, which is specialized for the active User 
model, the utilities herein allow for the dynamic resolution of any model 
registered within the Django App Registry. This is particularly useful for 
handling circular dependencies, building generic plugins, or interacting with 
models where the app_label is only known at runtime.

### **Usage**:
    from registry_utils import get_registered_model
    model = get_registered_model('app_label', 'model_name')
"""

from django.apps import apps
from django.db.models import Model
from django.core.exceptions import ImproperlyConfigured
from typing import Any, Type


def get_registered_model(app_label, model_name) ->Type[Model]:
    """
    Fetch a Django model class from the app registry using its app label 
    and model name.
    ----

    This function acts as a safety-wrapped proxy for **`apps.get_model()`**. 
    While **`apps.get_model()`** returns `None` if a model is not found—potentially 
    leading to confusing 'NoneType' errors later in execution—this function 
    raises an `ImproperlyConfigured` exception immediately to aid in debugging.

    ### **ARGS**:
    * **app_label** (str): The name of the Django app (e.g., 'auth').
    * **model_name** (str): The name of the model class (e.g., 'User').
    
    ### **RETURNS**:
        * **django.db.models.Model**: The resolved model class.

    ### **RAISES**:
        * **ImproperlyConfigured**: If the **app_label/model_name** combination 
        does not exist in the project's installed apps.
    """
    model = apps.get_model(app_label, model_name)
    
    if not model:
        raise ImproperlyConfigured(
            f"Could not find the model '{model_name}' in the app '{app_label}'. "
            f"Ensure the app is in INSTALLED_APPS and the model name is correct."
        )
        
    return model


def get_model_metadata(app_label: str, model_name: str) -> dict[str, Any]:
    """
    Extract key metadata for a model (fields, verbose names, etc.).

    ### **ARGS**:
    * **app_label** (str): The app label.
    * **model_name** (str): The model name.

    ### **RETURNS**:
    * **dict**: A dictionary containing 'verbose_name', 'table_name', and 'fields'.
    """
    model = get_registered_model(app_label, model_name)
    meta = model._meta
    
    return {
        "verbose_name": meta.verbose_name,
        "verbose_name_plural": meta.verbose_name_plural,
        "db_table": meta.db_table,
        "field_names": [f.name for f in meta.get_fields()],
    }