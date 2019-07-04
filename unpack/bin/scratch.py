# from pprint import pprint
# import inspect


# class Scrapper():
#     configs = {}

#     def __init__(self, config_name, download_cls=None, dispatch_cls=None, extract_cls=None):
#         self.update_config(config_name)
#         self.set_download_cls(download_cls)
#         self.set_dispatch_cls(dispatch_cls)
#         self.set_extract_cls(extract_cls)

#     @classmethod
#     def set_download_cls(cls, download_cls):
#         if download_cls:
#             cls.download_cls = download_cls
#         else:
#             cls.download_cls = Download

#     @classmethod
#     def set_dispatch_cls(cls, dispatch_cls):
#         if dispatch_cls:
#             cls.dispatch_cls = dispatch_cls
#         else:
#             cls.dispatch_cls = Dispatch

#     @classmethod
#     def set_extract_cls(cls, extract_cls):
#         cls.extract_cls = extract_cls

#     @classmethod
#     def update_config(cls, config_name):
#         if config_name == 'xkcd':
#             cls.config = {'site': 'http://xckd.fake'}
#         else:
#             cls.config = {'site': 'http://example.com'}

#     @classmethod
#     def extract(cls):
#         return cls.extract_cls(cls)

#     @classmethod
#     def dispatch(cls):
#         return cls.dispatch_cls(cls)

#     @classmethod
#     def download(cls):
#         return cls.download_cls(cls)


# class Extract():
#     def __init__(self, scrapper):
#         self.scrapper = scrapper

#     def run(self):
#         print('in Extract.run():')
#         self.do_extract()

#     def do_extract(self):
#         print('in my base do_extract')


# class Dispatch():
#     def __init__(self, scrapper):
#         self.scrapper = scrapper

#     def run(self, items):
#         print('in Dispatch.run():', self.scrapper.config, items)
#         self.scrapper.download().run()


# class Download():
#     def __init__(self, scrapper):
#         self.scrapper = scrapper

#     def run(self):
#         print('in Download.run():')
#         self.download()
#         self.scrapper.extract().run()

#     def download(self):
#         print('my base downloader')


# class XCKDDownload(Download):
#     def download(self):
#         print('my xkcd downloader')


# class XCKDExtract(Extract):
#     def do_extract(self):
#         print('my xkcd do_extract')

# xkcd_comic_scrapper = Scrapper(
#     config_name='xkcd',
#     download_cls=XCKDDownload,
#     extract_cls=XCKDExtract
# )
# xkcd_comics_dispatch = xkcd_comic_scrapper.dispatch()
# xkcd_comics_dispatch.run([1, 2, 3])

# xkcd_ex([
#     ex_task(arg1='foo', arg2='bar'),
#     ex_task(arg1='foo', arg2='bar'),
# ])
