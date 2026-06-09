with AUnit;
with AUnit.Assertions;
with AUnit.Test_Cases.Registration;
with Calculator;

package body Calculator_Test_Cases is
   use AUnit.Assertions;
   use AUnit.Test_Cases.Registration;

   overriding function Name (Test : Test_Case) return AUnit.Message_String is
      pragma Unreferenced (Test);
   begin
      return AUnit.Format ("Calculator unit tests");
   end Name;

   procedure Test_Add_Positive_Integers (Test : in out AUnit.Test_Cases.Test_Case'Class) is
      pragma Unreferenced (Test);
   begin
      Assert (Calculator.Add (2, 3) = 5, "Add must return the sum of two positive integers.");
   end Test_Add_Positive_Integers;

   procedure Test_Subtract_Can_Return_Negative_Value (Test : in out AUnit.Test_Cases.Test_Case'Class) is
      pragma Unreferenced (Test);
   begin
      Assert (Calculator.Subtract (3, 7) = -4, "Subtract must preserve negative results.");
   end Test_Subtract_Can_Return_Negative_Value;

   procedure Test_Divide_By_Zero_Raises_Domain_Exception (Test : in out AUnit.Test_Cases.Test_Case'Class) is
      pragma Unreferenced (Test);
   begin
      begin
         declare
            Ignored : constant Integer := Calculator.Divide (10, 0);
         begin
            pragma Unreferenced (Ignored);
            Assert (False, "Divide must raise Division_By_Zero for divisor zero.");
         end;
      exception
         when Calculator.Division_By_Zero =>
            null;
      end;
   end Test_Divide_By_Zero_Raises_Domain_Exception;

   overriding procedure Register_Tests (Test : in out Test_Case) is
   begin
      Register_Routine (Test, Test_Add_Positive_Integers'Access, "Add positive integers");
      Register_Routine (Test, Test_Subtract_Can_Return_Negative_Value'Access, "Subtract can return negative value");
      Register_Routine (Test, Test_Divide_By_Zero_Raises_Domain_Exception'Access, "Divide by zero raises domain exception");
   end Register_Tests;
end Calculator_Test_Cases;
