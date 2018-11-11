// Fill out your copyright notice in the Description page of Project Settings.

#include "Gaimer.h"

// Sets default values
AGaimer::AGaimer()
{
 	// Set this character to call Tick() every frame.  You can turn this off to improve performance if you don't need it.
	PrimaryActorTick.bCanEverTick = true;

}

// Called when the game starts or when spawned
void AGaimer::BeginPlay()
{
	Super::BeginPlay();

	mHtto = &FHttpModule::Get();

	SendInitRequest();
}

TSharedRef<IHttpRequest> AGaimer::CreateRequest(FString SubApi)
{
	TSharedRef<IHttpRequest> Request = mHtto->CreateRequest();
	FString api = mApiBaseUrl + SubApi;
	Request->SetURL(api);
	Request->SetHeader(TEXT("User-Agent"), TEXT("X-UnrealEngine-Agent"));
	Request->SetHeader(TEXT("Content-Type"), TEXT("application/json"));
	Request->SetHeader(TEXT("Accepts"), TEXT("application/json"));
	Request->SetVerb("GET");

	return Request;
}

void AGaimer::SendInitRequest()
{
	FString character = "kishore";
	FString init_game = "init_game?";
	init_game = init_game + FString("name=") + character;

	TSharedRef<IHttpRequest> Request = CreateRequest(init_game);

	Request->OnProcessRequestComplete().BindUObject(this, &AGaimer::OnInitComplete);
	Request->ProcessRequest();
}


// Called every frame
void AGaimer::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

}

// Called to bind functionality to input
void AGaimer::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
	Super::SetupPlayerInputComponent(PlayerInputComponent);

}

bool IsResponseGood(FHttpResponsePtr Response, bool bWasSuccessful)
{
	if (!bWasSuccessful || !Response.IsValid())
	{
		UE_LOG(LogTemp, Warning, TEXT("Http Failed"), Response->GetResponseCode());
		return false;
	}

	if (EHttpResponseCodes::IsOk(Response->GetResponseCode()))
	{
		return true;
	}
	else
	{
		UE_LOG(LogTemp, Warning, TEXT("Http Response returned error code: %d"), Response->GetResponseCode());
		return false;
	}
}

void AGaimer::OnInitComplete(FHttpRequestPtr Request, FHttpResponsePtr Response, bool bWasSuccessful)
{
	if (!IsResponseGood(Response, bWasSuccessful))
	{
		return;
	}

	GetStructFromJsonString<FGameDetails>(Response, mGameBeingWatched);

	UE_LOG(LogTemp, Warning, TEXT("Response is: %d"), mGameBeingWatched.num_plays);
}

void AGaimer::OnResponse(FHttpRequestPtr Request, FHttpResponsePtr Response, bool bWasSuccessful)
{
	if (IsResponseGood(Response, bWasSuccessful))
	{
		return;
	}

	UE_LOG(LogTemp, Warning, TEXT("Response is: %s"), *(Response->GetContentAsString()));
}

template <typename StructType>
void AGaimer::GetJsonStringFromStruct(StructType FilledStruct, FString& StringOutput) {
	FJsonObjectConverter::UStructToJsonObjectString(StructType::StaticStruct(), &FilledStruct, StringOutput, 0, 0);
}

template <typename StructType>
void AGaimer::GetStructFromJsonString(FHttpResponsePtr Response, StructType& StructOutput) {
	FString JsonString = Response->GetContentAsString();
	JsonString.ReplaceInline(TEXT("\'"), TEXT("\""));
	FJsonObjectConverter::JsonObjectStringToUStruct<StructType>(JsonString, &StructOutput, 0, 0);
}