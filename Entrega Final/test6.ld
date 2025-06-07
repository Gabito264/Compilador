program fibonacci_test;
 
var
    n, resultado : int;
 
 
void fib(n: int, a: int, b: int, count: int)[
    var tea : int;
    {
        if (count > 1) {
            tea = a + b;
            print("F(", count, ") = ", tea);
            fib(n, b, tea, count - 1);
        }
        else {
            print("Serie Fibonacci completada");
        };
    }
];
 
 
void iniciar_fibonacci(l: int)[
    {
        if (l > 0) {
            print("F(0) = 0");
            if (l > 1) {
                print("F(1) = 1");
                if (l > 2) {
                    fib(l, 0, 1, l - 1);
                };
            };
        }
        else {
            print("Error: l debe ser mayor que 0");
        };
    }
];
 
main {
    print("=== SERIE DE FIBONACCI ===");
 
  
    n = 5;
    print("Calculando Fibonacci hasta F(", n, "):");
    iniciar_fibonacci(n);
 
    print("");
 
   
    n = 8;
    print("Calculando Fibonacci hasta F(", n, "):");
    iniciar_fibonacci(n);
 
    print("");
    print("=== FIN DEL PROGRAMA ===");
}
end