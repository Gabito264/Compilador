program proquacks;
var n : int ;
  j , i : float;
  s : string;
 
void fact (n : int, a : int)
[  var b : int;
 
   {  if (n > 1 )
      {  b = a * n;
         fact (n-1, b); 
      }
      else
      {  print(a);   }; 
   }
];
 
void some_other( n : int )
[  var xf : float;
   {  @n = "woooooooooo 5"; 
      print("hello ", 7+5); 
      xf = 7;
 
      fact(6,1);
      
   } 
];
 
main 
{  n = -1;
   n = 5;
   fact(n, 1);
   some_other(10);
    do {
 
      print(3, "w", 4+5, 4.5);
    }while( 3 >5  );
 
 
    if ( 3 >= 8)
    {
      print("texto ");
      n = 58 + 9 * 5;
    }
    else
    {   print("xsxsxs", (5) );
 
    };
}
end