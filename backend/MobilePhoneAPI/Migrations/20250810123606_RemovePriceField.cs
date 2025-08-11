using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace MobilePhoneAPI.Migrations
{
    /// <inheritdoc />
    public partial class RemovePriceField : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(
                name: "Price",
                table: "Phones");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<decimal>(
                name: "Price",
                table: "Phones",
                type: "numeric(10,2)",
                nullable: true);
        }
    }
}
