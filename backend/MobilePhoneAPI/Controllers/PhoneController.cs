using Microsoft.AspNetCore.Mvc;
using MobilePhoneAPI.Models;
using MobilePhoneAPI.Services;

namespace MobilePhoneAPI.Controllers;

[ApiController]
[Route("api/[controller]")]
public class PhoneController : ControllerBase
{
    private readonly IPhoneService _phoneService;

    public PhoneController(IPhoneService phoneService)
    {
        _phoneService = phoneService;
    }

    // GET: api/phone
    [HttpGet]
    public async Task<ActionResult<List<Phone>>> GetAllPhones()
    {
        try
        {
            var phones = await _phoneService.GetAllPhonesAsync();
            return Ok(phones);
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { message = "Error loading phones data", error = ex.Message });
        }
    }

    // GET: api/phone/{id}
    [HttpGet("{id}")]
    public async Task<ActionResult<Phone>> GetPhoneById(int id)
    {
        try
        {
            var phone = await _phoneService.GetPhoneByIdAsync(id);
            if (phone == null)
            {
                return NotFound(new { message = "Phone not found" });
            }
            return Ok(phone);
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { message = "Error loading phone data", error = ex.Message });
        }
    }

    // GET: api/phone/search?term={searchTerm}
    [HttpGet("search")]
    public async Task<ActionResult<List<Phone>>> SearchPhones([FromQuery] string term)
    {
        try
        {
            var phones = await _phoneService.SearchPhonesAsync(term);
            return Ok(phones);
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { message = "Error searching phones", error = ex.Message });
        }
    }

    // GET: api/phone/brand/{brand}
    [HttpGet("brand/{brand}")]
    public async Task<ActionResult<List<Phone>>> GetPhonesByBrand(string brand)
    {
        try
        {
            var phones = await _phoneService.GetPhonesByBrandAsync(brand);
            return Ok(phones);
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { message = "Error loading phones by brand", error = ex.Message });
        }
    }

    // GET: api/phone/brands
    [HttpGet("brands")]
    public async Task<ActionResult<List<string>>> GetAllBrands()
    {
        try
        {
            var phones = await _phoneService.GetAllPhonesAsync();
            var brands = phones.Select(p => p.Brand).Distinct().OrderBy(b => b).ToList();
            return Ok(brands);
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { message = "Error loading brands", error = ex.Message });
        }
    }
} 