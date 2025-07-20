var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
// Learn more about configuring OpenAPI at https://aka.ms/aspnet/openapi
builder.Services.AddOpenApi();

var app = builder.Build();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.MapOpenApi();
}

app.UseHttpsRedirection();

// Sample phones data for testing
var samplePhones = new[]
{
    new Phone { Id = 1, Brand = "Apple", Model = "iPhone 15 Pro", Price = 999.99m },
    new Phone { Id = 2, Brand = "Samsung", Model = "Galaxy S24 Ultra", Price = 1199.99m },
    new Phone { Id = 3, Brand = "Google", Model = "Pixel 8 Pro", Price = 899.99m }
};

// Test API endpoint for phones
app.MapGet("/api/phones", () =>
{
    return samplePhones;
})
.WithName("GetPhones");

// Test API endpoint for specific phone
app.MapGet("/api/phones/{id}", (int id) =>
{
    var phone = samplePhones.FirstOrDefault(p => p.Id == id);
    return phone != null ? Results.Ok(phone) : Results.NotFound();
})
.WithName("GetPhoneById");

// Health check endpoint
app.MapGet("/api/health", () =>
{
    return new { Status = "Healthy", Message = "Mobile Phone API is running!", Timestamp = DateTime.UtcNow };
})
.WithName("HealthCheck");

app.Run();

// Phone model for testing
public class Phone
{
    public int Id { get; set; }
    public string Brand { get; set; } = string.Empty;
    public string Model { get; set; } = string.Empty;
    public decimal Price { get; set; }
}
