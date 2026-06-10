using System.Xml.Linq;
using FlaUI.Core.AutomationElements;

namespace Product.UiTests.Shared.Diagnostics;

public static class UiaTreeDumper
{
    public static void Dump(Window window, string outputPath)
    {
        var root = DumpElement(window, depth: 0);
        Directory.CreateDirectory(Path.GetDirectoryName(outputPath)!);
        new XDocument(root).Save(outputPath);
    }

    private static XElement DumpElement(AutomationElement element, int depth)
    {
        var properties = element.Properties;
        var node = new XElement("Element",
            new XAttribute("Depth", depth),
            new XAttribute("Name", properties.Name.ValueOrDefault ?? string.Empty),
            new XAttribute("AutomationId", properties.AutomationId.ValueOrDefault ?? string.Empty),
            new XAttribute("ControlType", properties.ControlType.ValueOrDefault?.ToString() ?? string.Empty),
            new XAttribute("ClassName", properties.ClassName.ValueOrDefault ?? string.Empty));

        foreach (var child in element.FindAllChildren())
        {
            node.Add(DumpElement(child, depth + 1));
        }

        return node;
    }
}
