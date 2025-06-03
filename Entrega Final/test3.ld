program proquacks;
var n: int;
void print_stuff (n: int, a:float)
[ var b: string;
    {   
        b = "Hello";
        print(n);
        print(a);
        print(b);
        print(n+1," " ,b," ", a+1);
    }
];

main {
    print("Let's print some stuff!");
    print_stuff(4, 4.5);
}
end