program proquacks;
var 
        A, B, C, D : int ; F : string;
main {
    A = 7;
    B = 1;
    C = B;
    D = 10;

    if (A + B > D)
    {
        if (A < B)
        {
            A = 0;
            B = B + D;
        }
        else
        {
            C = A + B;
        };
    }
    else
    {
        A = B + C;
    };
    D = B + A * C;
} end