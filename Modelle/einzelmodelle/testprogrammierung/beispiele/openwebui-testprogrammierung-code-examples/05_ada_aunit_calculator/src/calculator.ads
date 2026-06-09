package Calculator is
   Division_By_Zero : exception;

   function Add (Left, Right : Integer) return Integer;
   function Subtract (Left, Right : Integer) return Integer;
   function Divide (Dividend, Divisor : Integer) return Integer;
end Calculator;
