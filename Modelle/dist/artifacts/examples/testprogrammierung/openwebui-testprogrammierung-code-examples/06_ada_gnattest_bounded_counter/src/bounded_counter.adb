package body Bounded_Counter is
   function Create (Minimum, Maximum, Initial : Integer) return Counter is
   begin
      return (Min => Minimum, Max => Maximum, Val => Initial);
   end Create;

   function Value (Item : Counter) return Integer is
   begin
      return Item.Val;
   end Value;

   function Minimum (Item : Counter) return Integer is
   begin
      return Item.Min;
   end Minimum;

   function Maximum (Item : Counter) return Integer is
   begin
      return Item.Max;
   end Maximum;

   procedure Increment (Item : in out Counter) is
   begin
      if Item.Val = Item.Max then
         raise Capacity_Error;
      end if;

      Item.Val := Item.Val + 1;
   end Increment;

   procedure Decrement (Item : in out Counter) is
   begin
      if Item.Val = Item.Min then
         raise Capacity_Error;
      end if;

      Item.Val := Item.Val - 1;
   end Decrement;
end Bounded_Counter;
