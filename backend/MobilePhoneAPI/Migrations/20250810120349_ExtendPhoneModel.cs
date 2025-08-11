using Microsoft.EntityFrameworkCore.Migrations;
using Npgsql.EntityFrameworkCore.PostgreSQL.Metadata;

#nullable disable

namespace MobilePhoneAPI.Migrations
{
    /// <inheritdoc />
    public partial class ExtendPhoneModel : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "Phones",
                columns: table => new
                {
                    Id = table.Column<int>(type: "integer", nullable: false)
                        .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                    Brand = table.Column<string>(type: "character varying(50)", maxLength: 50, nullable: false),
                    Model = table.Column<string>(type: "character varying(100)", maxLength: 100, nullable: false),
                    Storage = table.Column<string>(type: "character varying(50)", maxLength: 50, nullable: false),
                    Ram = table.Column<string>(type: "character varying(20)", maxLength: 20, nullable: false),
                    ScreenSize = table.Column<string>(type: "character varying(20)", maxLength: 20, nullable: false),
                    Camera = table.Column<string>(type: "character varying(100)", maxLength: 100, nullable: false),
                    Battery = table.Column<string>(type: "character varying(20)", maxLength: 20, nullable: false),
                    Price = table.Column<decimal>(type: "numeric(10,2)", nullable: false),
                    ImageUrl = table.Column<string>(type: "character varying(255)", maxLength: 255, nullable: false),
                    Weight = table.Column<decimal>(type: "numeric(5,2)", nullable: true),
                    Dimensions = table.Column<string>(type: "character varying(50)", maxLength: 50, nullable: true),
                    Processor = table.Column<string>(type: "character varying(100)", maxLength: 100, nullable: true),
                    Os = table.Column<string>(type: "character varying(50)", maxLength: 50, nullable: true),
                    ReleaseYear = table.Column<int>(type: "integer", nullable: true),
                    NetworkType = table.Column<string>(type: "character varying(50)", maxLength: 50, nullable: true),
                    ChargingPower = table.Column<string>(type: "character varying(20)", maxLength: 20, nullable: true),
                    WaterResistance = table.Column<string>(type: "character varying(20)", maxLength: 20, nullable: true),
                    Material = table.Column<string>(type: "character varying(50)", maxLength: 50, nullable: true),
                    Colors = table.Column<string>(type: "character varying(200)", maxLength: 200, nullable: true),
                    ImageFront = table.Column<string>(type: "character varying(255)", maxLength: 255, nullable: true),
                    ImageBack = table.Column<string>(type: "character varying(255)", maxLength: 255, nullable: true),
                    ImageSide = table.Column<string>(type: "character varying(255)", maxLength: 255, nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Phones", x => x.Id);
                });

            migrationBuilder.CreateIndex(
                name: "IX_Phones_Brand",
                table: "Phones",
                column: "Brand");

            migrationBuilder.CreateIndex(
                name: "IX_Phones_Model",
                table: "Phones",
                column: "Model");

            migrationBuilder.CreateIndex(
                name: "IX_Phones_ReleaseYear",
                table: "Phones",
                column: "ReleaseYear");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "Phones");
        }
    }
}
