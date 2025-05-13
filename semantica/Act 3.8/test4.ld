program condition_function;
var 
        A, B, C: int ;
main {
    A = 10;
    B = A;
    C = 5;

    if (C == A){
        C = A+B;
    };
    A = C*10;
} end