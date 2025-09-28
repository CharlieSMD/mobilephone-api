using Microsoft.AspNetCore.Mvc;
using MobilePhoneAPI.Services;

namespace MobilePhoneAPI.Controllers;

[ApiController]
[Route("api/[controller]")]
public class DataImportController : ControllerBase
{
    private readonly IDataImportService _dataImportService;

    public DataImportController(IDataImportService dataImportService)
    {
        _dataImportService = dataImportService;
    }

    [HttpPost("import-phones")]
    public async Task<ActionResult<ImportResult>> ImportPhonesFromCsv()
    {
        try
        {
            // Path to CSV file (relative to project root)
            var csvFilePath = Path.Combine(Directory.GetCurrentDirectory(), "complete_phones_final.csv");
            
            var importedCount = await _dataImportService.ImportPhonesFromCsvAsync(csvFilePath);
            
            return Ok(new ImportResult
            {
                Success = true,
                Message = $"Successfully imported {importedCount} phones from CSV file",
                ImportedCount = importedCount
            });
        }
        catch (FileNotFoundException ex)
        {
            return NotFound(new ImportResult
            {
                Success = false,
                Message = ex.Message,
                ImportedCount = 0
            });
        }
        catch (Exception ex)
        {
            return StatusCode(500, new ImportResult
            {
                Success = false,
                Message = $"Error importing data: {ex.Message}",
                ImportedCount = 0
            });
        }
    }

    [HttpGet("status")]
    public ActionResult<ImportStatus> GetImportStatus()
    {
        try
        {
            var csvFilePath = Path.Combine(Directory.GetCurrentDirectory(), "complete_phones_final.csv");
            var fileExists = System.IO.File.Exists(csvFilePath);
            
            return Ok(new ImportStatus
            {
                CsvFileExists = fileExists,
                CsvFilePath = csvFilePath,
                Message = fileExists ? "CSV file found" : "CSV file not found"
            });
        }
        catch (Exception ex)
        {
            return StatusCode(500, new ImportStatus
            {
                CsvFileExists = false,
                CsvFilePath = "",
                Message = $"Error checking status: {ex.Message}"
            });
        }
    }
}

public class ImportResult
{
    public bool Success { get; set; }
    public string Message { get; set; } = string.Empty;
    public int ImportedCount { get; set; }
}

public class ImportStatus
{
    public bool CsvFileExists { get; set; }
    public string CsvFilePath { get; set; } = string.Empty;
    public string Message { get; set; } = string.Empty;
}

