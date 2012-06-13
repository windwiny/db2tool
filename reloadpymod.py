#-*- coding:utf-8 -*-

def install():
    reloadmodtxt = """
'''
-----------------------------------------------------------------------------
 Reload module, and auto change all wrap class's instance.__class__.__bases__

 1. On everyone module
   1) create wrap Class, in __init__/<or other> call incInstance(self)
   2) set _WRAP_CLASS = <wrap Class>

   eg.
        # read reload module testcase
        import __builtin__
        if 'g_reloadmod' in __builtin__.__dict__:
            class MainFrame(_ori_MainFrame):
                def __init__(self, *args, **kwargs):
                    super(MainFrame, self).__init__(*args, **kwargs)
                    incInstance(self)

            _WRAP_CLASS = MainFrame

            exec(g_reloadmod)
        else:
            MainFrame = _ori_MainFrame

 2. On Main program
   1) create _WRAP_CLASS's instance

   eg.
        import xxx
        obj1 = xxx.MainFrame(...)

 3. On Main program, test and reload modules code

    eg.
        def OnReloadModules(*args):
            try:
                import reloadpymod
                reloadpymod.reloadall()
            except:
                pass

 State:
   Create a object, origin class inherit:
     obj1 ==>  WrapClass1 -> RealClass1 -> Other -> object

   After reload:
     obj1 ==>  WrapClass1 -> WrapClass1 -> RealClass1 -> Other -> object
                ^create time's  ^reload
        -> super(WrapClass1, self).func1(...) # <- WrapClass1 is reload
        -> WrapClass1).func1(self, ...)       # <- WrapClass1 is reload

-----------------------------------------------------------------------------
'''

# ---- reload module, update object bases -----------------------------------
import weakref
import time

_loadtime = time.time()
_REAL_CLASS = _WRAP_CLASS.__bases__[0]

def incInstance(inst1):
    global g_objs
    try:
        g_objs
    except NameError:
        g_objs = []
    g_objs.append(weakref.ref(inst1, decInstance))
    print 'R: new <%s.%s> instance %d.  [%2d]' % (__name__,
        _WRAP_CLASS.__name__, id(inst1.__class__.__bases__[0]), len(g_objs))

def decInstance(ref1):
    global g_objs
    try:
        g_objs
    except NameError:
        return
    try:
        if ref1 in g_objs:
            g_objs.remove(ref1)
            print 'R: remove <%s.%s> instance ref.  [%2d]' % (
                __name__, _WRAP_CLASS.__name__, len(g_objs))
    except AttributeError:  # on exit, module scope objs destroy order
        pass

try:
    # if has g_objs, replace all instance class bases
    g_objs

    rs = 0
    for ref_ in g_objs:
        obj1_ = ref_()
        if not obj1_:
            continue

        obs_ = []
        iSameName = 0
        for c_ in obj1_.__class__.__bases__:
            if(c_.__name__ == _REAL_CLASS.__name__ or
               c_.__name__ == _WRAP_CLASS.__name__ and not c_ is _WRAP_CLASS):
                obs_.append(_WRAP_CLASS)
                rs += 1
                iSameName += 1
            else:
                obs_.append(c_)
        assert iSameName <= 1
        obj1_.__class__.__bases__ = tuple(obs_)
    print "R: old <%s.%s> instance %d. replace %d ok" % (__name__,
        _WRAP_CLASS.__name__, len(g_objs), rs)

    ids = set()
    for ref_ in g_objs:
        obj1_ = ref_()
        if not obj1_: continue
        for c_ in obj1_.__class__.__bases__:
            if c_.__name__ == _WRAP_CLASS.__name__:
                ids.add(id(c_))
                break
    ids = list(ids)
    if len(ids) == 1:
        print 'R: review. g_objs: %d id: %s' % (len(g_objs), str(ids))
    else:
        print '!!!! R: review. g_objs: %d id: %s' % (len(g_objs), str(ids))
except NameError:
    print 'R: load <%s.%s>.' % (__name__, _WRAP_CLASS.__name__)
# ---- reload end. -----------------------------------------------------------
"""

    import __builtin__
    __builtin__.__dict__['g_reloadmod'] = compile(reloadmodtxt, __file__, 'exec')

def reloadall():
    import sys
    import os
    import types

    def reloadmod(mod, maxlevel=2):
        print ' test', mod.__name__
        fn = os.path.abspath(mod.__file__)
        fn2 = fn.rstrip('co')
        fn = fn2 if os.path.isfile(fn2) else fn
        if not os.path.isfile(fn):
            return
        if os.path.getmtime(fn) > mod._loadtime:
            print 'reload ', mod.__name__, mod.__file__, mod._loadtime
            reload(mod)
        if maxlevel == 0: return
        for it in dir(mod):
            mod2 = getattr(mod, it)
            if type(mod2) is types.ModuleType and hasattr(mod2, '_loadtime'):
                reloadmod(mod2, maxlevel-1)
    print '---------------------'
    for i in sys.modules:
        mod = sys.modules[i]
        if type(mod) is types.ModuleType and hasattr(mod, '_loadtime'):
            reloadmod(mod, 2)
    print '---------------------'
