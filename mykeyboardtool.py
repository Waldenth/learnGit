
import PyHook3
import pythoncom
import pykeyboard
import time
import win32api
from colorama import init
init(autoreset=True)


k = pykeyboard.PyKeyboard()
# print(dir(k))


# press_and_hold('W', 1)
def press_and_hold(character, hold_time):
    k.press_key(character)
    time.sleep(hold_time)
    k.release_key(character)


def tap_break(intervalTime):
    k.tap_key(k.up_key, n=10, interval=intervalTime)
    k.tap_key('o')


def changeCarry_break(intervalTime, changeNum):
    k.tap_key(k.right_key, n=changeNum, interval=intervalTime)
    k.tap_key(k.up_key, n=4, interval=intervalTime)
    k.tap_key('o')


# 鼠标事件处理函数
def OnMouseEvent(event):
    print('MessageName:', event.MessageName)  # 事件名称
    print('Message:', event.Message)  # windows消息常量
    print('Time:', event.Time)  # 事件发生的时间戳
    print('Window:', event.Window)  # 窗口句柄
    print('WindowName:', event.WindowName)  # 窗口标题
    print('Position:', event.Position)  # 事件发生时相对于整个屏幕的坐标
    print('Wheel:', event.Wheel)  # 鼠标滚轮
    print('Injected:', event.Injected)  # 判断这个事件是否由程序方式生成，而不是正常的人为触发。
    print('---')
    # 返回True代表将事件继续传给其他句柄，为False则停止传递，即被拦截
    return True


def printKeyBoardEventInfo(event):
    print('MessageName:', event.MessageName)  # 同上，共同属性不再赘述
    print('Message:', event.Message)
    print('Time:', event.Time)
    print('Window:', event.Window)
    print('WindowName:', event.WindowName)
    print('Ascii:', event.Ascii, chr(event.Ascii))  # 按键的ASCII码
    print('Key:', event.Key)  # 按键的名称
    print('KeyID:', event.KeyID)  # 按键的虚拟键值
    print('ScanCode:', event.ScanCode)  # 按键扫描码
    print('Extended:', event.Extended)  # 判断是否为增强键盘的扩展键
    print('Injected:', event.Injected)
    print('Alt', event.Alt)  # 是某同时按下Alt
    print('Transition', event.Transition)  # 判断转换状态
    print('---')


# 键盘事件处理函数
def OnKeyboardEvent(event):
    # printKeyBoardEventInfo(event)
    if(event.KeyID == 32):  # space
        tap_break(0.01)
        print(f"\033[1;34;47muse space marco: Break\033[0m")
    elif(event.KeyID == 161):  # RightShift
        changeCarry_break(0.01, 1)
        print(f"\033[1;34;47muse Right shift marco: Change Carry Break\033[0m")
    elif(event.KeyID == 27):
        win32api.PostQuitMessage()
        print(f"\033[1;31;47mexit monitor\033[0m")

    # 同上
    return True


def main():
    # 创建一个“钩子”管理对象ass
    hm = PyHook3.HookManager()
    # 设置键盘“钩子”
    hm.KeyDown = OnKeyboardEvent
    hm.HookKeyboard()

    # 进入循环，如不手动关闭，程序将一直处于监听状态
    pythoncom.PumpMessages()
    print(f"\033[1;31;47mThe program will exit after 3.0s\033[0m")
    time.sleep(3)
    print(f"\033[1;31;47mexit program\033[0m")


if __name__ == "__main__":
    main()
