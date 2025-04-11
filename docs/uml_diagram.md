# Library Management System - UML Diagram

This document provides a UML class diagram for the Library Management System.

## Class Diagram

```plantuml
@startuml

package "Models" {
  class Book {
    + id: Integer
    + title: String
    + author: String
    + isbn: String
    + category: String
    + publication_year: Integer
    + description: Text
    + available: Boolean
    + created_at: DateTime
    + updated_at: DateTime
    --
    + is_available(): Boolean
    + to_dict(): Dictionary
  }
  
  class Member {
    + id: Integer
    + first_name: String
    + last_name: String
    + email: String
    + phone: String
    + address: String
    + registration_date: DateTime
    + active: Boolean
    + created_at: DateTime
    + updated_at: DateTime
    --
    + full_name(): String
    + count_active_loans(): Integer
    + has_overdue_loans(): Boolean
    + to_dict(): Dictionary
  }
  
  class Loan {
    + id: Integer
    + book_id: Integer
    + member_id: Integer
    + loan_date: DateTime
    + due_date: DateTime
    + return_date: DateTime
    + returned: Boolean
    + notes: Text
    + created_at: DateTime
    + updated_at: DateTime
    --
    + is_overdue(): Boolean
    + days_overdue(): Integer
    + calculate_fine(daily_rate: Float): Float
    + return_book(): Boolean
    + to_dict(): Dictionary
    --
    {static} create_loan(book_id: Integer, member_id: Integer, loan_period_days: Integer): Loan
  }
}

package "Routes" {
  class BookRoutes {
    + index(): Response
    + create(): Response
    + show(id: Integer): Response
    + edit(id: Integer): Response
    + delete(id: Integer): Response
  }
  
  class MemberRoutes {
    + index(): Response
    + create(): Response
    + show(id: Integer): Response
    + edit(id: Integer): Response
    + delete(id: Integer): Response
  }
  
  class LoanRoutes {
    + index(): Response
    + create(): Response
    + show(id: Integer): Response
    + return_book(id: Integer): Response
    + overdue_check(): Response
    + upcoming_due(): Response
  }
  
  class APIRoutes {
    + get_books(): Response
    + get_book(id: Integer): Response
    + create_book(): Response
    + update_book(id: Integer): Response
    + delete_book(id: Integer): Response
    + get_members(): Response
    + get_member(id: Integer): Response
    + create_member(): Response
    + update_member(id: Integer): Response
    + delete_member(id: Integer): Response
    + get_loans(): Response
    + get_loan(id: Integer): Response
    + create_loan(): Response
    + api_return_book(id: Integer): Response
    + get_statistics(): Response
  }
}

package "Utils" {
  class Notifications {
    {static} + send_notification(recipient_email: String, subject: String, message: String): Boolean
    {static} + send_overdue_notification(loan: Loan): Boolean
    {static} + send_upcoming_due_reminder(loan: Loan): Boolean
    {static} + send_return_confirmation(loan: Loan): Boolean
  }
}

Book "1" -- "0..*" Loan : has >
Member "1" -- "0..*" Loan : borrows >

BookRoutes --> Book : manages >
MemberRoutes --> Member : manages >
LoanRoutes --> Loan : manages >
APIRoutes --> Book : manages >
APIRoutes --> Member : manages >
APIRoutes --> Loan : manages >

Notifications --> Loan : uses >
Notifications --> Book : uses >
Notifications --> Member : uses >

@enduml
