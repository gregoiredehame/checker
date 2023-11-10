from PySide2.QtCore import QProcess as PySide2QProcess


class QProcess:
    @staticmethod
    def get_out_put(cmd):
        process = PySide2QProcess()
        process.start(cmd)
        process.waitForFinished()
        out_put = process.readAllStandardOutput()
        out_put = out_put.data()
        try:
            out_put = out_put.decode('utf-8')
        except UnicodeDecodeError:
            out_put = out_put.decode('gbk')
        finally:
            return out_put