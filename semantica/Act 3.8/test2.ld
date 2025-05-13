program error_handling;
var 
        A, B, C, D : int ; F: string;
main {
    @Darle un float a int no dará error, pero se truncará más adelante
    A = 7.5;
    @B no puede ser un booleano si este es int
    B = 1 < 5;
    @ No podemos asignar un valor que no sea string a un string
    F = 234;
} end