class Testes:
    def fatorial(self, n):
        if n == 0 or n == 1:
            return 1
        else:
            return n * self.fatorial(n - 1)


t = Testes()
print(t.fatorial(5))
