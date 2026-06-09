with AUnit.Test_Suites;
with Calculator_Test_Cases;

package body Calculator_Suite is
   function Suite return AUnit.Test_Suites.Access_Test_Suite is
      Result : constant AUnit.Test_Suites.Access_Test_Suite := AUnit.Test_Suites.New_Suite;
   begin
      -- Each Ada package under test should be represented by its own test case package.
      Result.Add_Test (new Calculator_Test_Cases.Test_Case);
      return Result;
   end Suite;
end Calculator_Suite;
