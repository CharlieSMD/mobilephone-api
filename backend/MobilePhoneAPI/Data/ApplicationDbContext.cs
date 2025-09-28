using Microsoft.EntityFrameworkCore;
using MobilePhoneAPI.Models;

namespace MobilePhoneAPI.Data;

public class ApplicationDbContext : DbContext
{
    public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options) : base(options)
    {
    }

    public DbSet<User> Users { get; set; }
    public DbSet<Phone> Phones { get; set; }
    public DbSet<Favorite> Favorites { get; set; }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        // User configuration
        modelBuilder.Entity<User>(entity =>
        {
            entity.ToTable("Users"); // Explicitly specify table name
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Username).IsRequired().HasMaxLength(50);
            entity.Property(e => e.Email).IsRequired().HasMaxLength(100);
            entity.Property(e => e.PasswordHash).IsRequired().HasMaxLength(255);
            entity.Property(e => e.FirstName).HasMaxLength(50);
            entity.Property(e => e.LastName).HasMaxLength(50);
            
            entity.HasIndex(e => e.Username).IsUnique();
            entity.HasIndex(e => e.Email).IsUnique();
        });

        // Phone configuration
        modelBuilder.Entity<Phone>(entity =>
        {
            entity.ToTable("Phones"); // Explicitly specify table name
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Brand).IsRequired().HasMaxLength(50);
            entity.Property(e => e.Model).IsRequired().HasMaxLength(100);
            entity.Property(e => e.Storage).HasMaxLength(50);
            entity.Property(e => e.Ram).HasMaxLength(20);
            entity.Property(e => e.ScreenSize).HasMaxLength(20);
            entity.Property(e => e.Camera).HasMaxLength(100);
            entity.Property(e => e.Battery).HasMaxLength(20);
            entity.Property(e => e.ImageUrl).HasMaxLength(255);
            
            // New fields configuration
            entity.Property(e => e.Weight).HasColumnType("decimal(5,2)");
            entity.Property(e => e.Dimensions).HasMaxLength(50);
            entity.Property(e => e.Processor).HasMaxLength(100);
            entity.Property(e => e.Os).HasMaxLength(50);
            entity.Property(e => e.NetworkType).HasMaxLength(50);
            entity.Property(e => e.ChargingPower).HasMaxLength(20);
            entity.Property(e => e.WaterResistance).HasMaxLength(20);
            entity.Property(e => e.Material).HasMaxLength(50);
            entity.Property(e => e.Colors).HasMaxLength(200);
            entity.Property(e => e.ColorImages).HasMaxLength(2000);
            entity.Property(e => e.ImageFront).HasMaxLength(255);
            entity.Property(e => e.ImageBack).HasMaxLength(255);
            entity.Property(e => e.ImageSide).HasMaxLength(255);
            
            // Create indexes for better performance
            entity.HasIndex(e => e.Brand);
            entity.HasIndex(e => e.Model);
            entity.HasIndex(e => e.ReleaseYear);
        });

        // Favorite configuration
        modelBuilder.Entity<Favorite>(entity =>
        {
            entity.ToTable("Favorites"); // Explicitly specify table name
            entity.HasKey(e => e.Id);
            entity.Property(e => e.CreatedAt).IsRequired();
            
            // Create unique index to prevent duplicate favorites
            entity.HasIndex(e => new { e.UserId, e.PhoneId }).IsUnique();
            
            // Foreign key relationships
            entity.HasOne(e => e.User)
                  .WithMany()
                  .HasForeignKey(e => e.UserId)
                  .OnDelete(DeleteBehavior.Cascade);
                  
            entity.HasOne(e => e.Phone)
                  .WithMany()
                  .HasForeignKey(e => e.PhoneId)
                  .OnDelete(DeleteBehavior.Cascade);
        });
    }
} 