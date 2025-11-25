import os
import streamlit.components.v1 as components

_RELEASE = True

if not _RELEASE:
    _component_func = components.declare_component(
        "circle_diagram",
        url="http://localhost:3000",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component("circle_diagram", path=build_dir)


def circle_diagram(key=None):
    """
    Create a Circle Diagram component.
    
    Returns dict with defect data when user completes the workflow.
    """
    component_value = _component_func(key=key, default=None)
    return component_value