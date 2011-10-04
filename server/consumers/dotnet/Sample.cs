using System;
using WebLabDeusto;

namespace Sample
{

    public class WebLabDeustoSample 
    {
        public static void Main(string [] args)
        {
            WebLabDeustoClient weblab = new WebLabDeustoClient("http://localhost/weblab/");

            SessionId sessionId = weblab.Login("any", "password");

            Reservation reservation = weblab.ReserveExperiment(sessionId, "ud-logic", "PIC experiments", "{}");

            Console.WriteLine(reservation);

            // Optional:
            ReservationId reservationId = reservation.ReservationId;
            reservation = weblab.GetReservationStatus(reservationId);

            Console.WriteLine(reservation);

            Console.WriteLine(weblab.CreateClient(reservation));
        }
    }
}

