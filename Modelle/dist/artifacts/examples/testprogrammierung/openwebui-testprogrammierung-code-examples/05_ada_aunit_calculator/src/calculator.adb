package body Calculator is
   function Add (Left, Right : Integer) return Integer is
   begin
      return Left + Right;
   end Add;

   function Subtract (Left, Right : Integer) return Integer is
   begin
      return Left - Right;
   end Subtract;

   function Divide (Dividend, Divisor : Integer) return Integer is
   begin
      if Divisor = 0 then
         raise Division_By_Zero;
      end if;

      return Dividend / Divisor;
   end Divide;
end Calculator;
