program proquacks;
var n: int;
void fact (N: int, a:int)
[ var b:int;
    {
        if (N>1)
        {
            b = a * N;
            fact (N-1, b);
        }
        else {
            print(a);
        };
    }
];

main {
    n = 5;
    fact(n, 1);
    fact(n+1, 1);
}
end