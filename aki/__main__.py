if __name__ == "__main__":
    import sys
    init_modules = set(sys.modules.keys())

    while True:
        from errors import ReloadException, QuitException
        from repl import repl    
        try:
            repl.run()
        except ReloadException:
            for m in reversed(list(sys.modules.keys())):
                if m not in init_modules:
                    del sys.modules[m]
            continue
        except QuitException:
            break