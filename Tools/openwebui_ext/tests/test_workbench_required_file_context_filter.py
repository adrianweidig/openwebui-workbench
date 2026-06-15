import unittest

from Tools.openwebui_ext.filters.workbench_required_file_context_filter import Filter


class WorkbenchRequiredFileContextFilterTests(unittest.IsolatedAsyncioTestCase):
    async def test_injects_context_from_openwebui_info_meta_model_shape(self) -> None:
        filter_instance = Filter()
        self.assertFalse(filter_instance.toggle)
        body = {"messages": [{"role": "user", "content": "Test"}]}
        model = {
            "id": "codegenerierung",
            "info": {
                "meta": {
                    "workbenchFileContext": {
                        "requiredFiles": [
                            {
                                "filename": "Golden_Example.py",
                                "content": "class Task:\n    pass",
                            }
                        ],
                        "uploadedFiles": [
                            {
                                "fileId": "file-123",
                                "filename": "Golden_Example.py",
                            }
                        ],
                    }
                }
            },
        }

        result = await filter_instance.inlet(body, __model__=model)

        self.assertEqual(result["messages"][0]["role"], "system")
        self.assertIn("## Workbench-Pflichtdateien", result["messages"][0]["content"])
        self.assertIn("### Datei: Golden_Example.py", result["messages"][0]["content"])
        self.assertIn("class Task", result["messages"][0]["content"])
        self.assertEqual(result["files"], [{"type": "file", "id": "file-123"}])


if __name__ == "__main__":
    unittest.main()
