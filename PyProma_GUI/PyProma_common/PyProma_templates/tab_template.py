from abc import ABC
from functools import wraps
from tkinter import Frame
from typing import Any, Callable, TypeVar

SelfType = TypeVar("SelfType", bound="TabTemplate")


class TabTemplate(ABC, Frame):
    def __init__(self, master=None, main=None):
        self.main = main
        super().__init__(master, width=800, height=575)
        self.propagate(False)

    @staticmethod
    def RefreshMethod(
            method: Callable[[SelfType], Any]) -> Callable[[SelfType], Any]:
        """This wrapper adds flag "__is_refresh_method__".
        The method wrapped by this func will be called
        when "main.refresh_trees()" was called.

        Args:
            method (Callable[[SelfType], Any]): The method you wrapped.

        Returns:
            Callable[[SelfType], Any]: The returns of your method.
        """
        setattr(method, "__is_refresh_method__", True)

        @wraps(method)
        def wrapper(self: SelfType):
            return method(self)
        return wrapper

    @staticmethod
    def PyFileMethod(method: Callable[[SelfType, str], Any]) \
            -> Callable[[SelfType, str], Any]:
        """This wrapper adds flag "__is_pyfile_method__".
        The method wrapped by this func will be called
        when ".py" file was found in project directory.

        Args:
            method (Callable[[SelfType, str], Any]): The method you wrapped.

        Returns:
            Callable[[SelfType, str], Any]: The returns of your method.
        """
        setattr(method, "__is_pyfile_method__", True)

        @wraps(method)
        def wrapper(self: SelfType, path: str):
            return method(self, path)
        return wrapper
