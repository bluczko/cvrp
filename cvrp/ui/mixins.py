class OnCloseCallbackMixin:
    __on_close_callback = None

    def set_on_close(self, callback: callable):
        self.__on_close_callback = callback

    def on_close(self):
        if self.__on_close_callback is not None:
            self.__on_close_callback()
