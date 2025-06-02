program arithmetic_functions;
var 
        A, B, C, D : int ; F: float;
main {
    A = 7;
    B = 8;
    if(A<B){
        print("B es Mejor");
    } else {
        print("A es Mejor");
    };
    print("I am out");

    print("here comes a counter");
    F = 0;
    do{
        F = F+1;
        print(F);
    }while(F < 10);
} end