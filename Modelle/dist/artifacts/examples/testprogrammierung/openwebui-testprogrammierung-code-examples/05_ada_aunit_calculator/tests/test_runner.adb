with AUnit;
with AUnit.Reporter.Text;
with AUnit.Run;
with Calculator_Suite;
with GNAT.OS_Lib;

procedure Test_Runner is
   function Run is new AUnit.Run.Test_Runner_With_Status (Calculator_Suite.Suite);
   Reporter : AUnit.Reporter.Text.Text_Reporter;
   Status   : AUnit.Status;
begin
   -- Test_Runner_With_Status lets CI receive a failing process exit code when assertions fail.
   Status := Run (Reporter);

   if Status = AUnit.Failure then
      GNAT.OS_Lib.OS_Exit (1);
   end if;
end Test_Runner;
