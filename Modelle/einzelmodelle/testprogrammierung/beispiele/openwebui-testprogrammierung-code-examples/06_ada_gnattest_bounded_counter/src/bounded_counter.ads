package Bounded_Counter is
   Capacity_Error : exception;

   type Counter is private;

   function Create (Minimum, Maximum, Initial : Integer) return Counter
     with Pre => Minimum <= Maximum and then Minimum <= Initial and then Initial <= Maximum;

   function Value (Item : Counter) return Integer;
   function Minimum (Item : Counter) return Integer;
   function Maximum (Item : Counter) return Integer;

   procedure Increment (Item : in out Counter);
   procedure Decrement (Item : in out Counter);

private
   type Counter is record
      Min : Integer;
      Max : Integer;
      Val : Integer;
   end record;
end Bounded_Counter;
