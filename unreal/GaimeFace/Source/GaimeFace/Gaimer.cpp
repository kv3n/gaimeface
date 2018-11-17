// Fill out your copyright notice in the Description page of Project Settings.

#include "Gaimer.h"

// Sets default values
AGaimer::AGaimer()
{
	mApiBaseUrl = "http://127.0.0.1:5000/";

	ResetGame();

 	// Set this character to call Tick() every frame.  You can turn this off to improve performance if you don't need it.
	PrimaryActorTick.bCanEverTick = true;

}

// Called when the game starts or when spawned
void AGaimer::BeginPlay()
{
	Super::BeginPlay();

	mHttp = &FHttpModule::Get();

	RequestStartGame("kishore");
}

TSharedRef<IHttpRequest> AGaimer::CreateRequest(FString SubApi)
{
	TSharedRef<IHttpRequest> Request = mHttp->CreateRequest();
	FString api = mApiBaseUrl + SubApi;
	Request->SetURL(api);
	Request->SetHeader(TEXT("User-Agent"), TEXT("X-UnrealEngine-Agent"));
	Request->SetHeader(TEXT("Content-Type"), TEXT("application/json"));
	Request->SetHeader(TEXT("Accepts"), TEXT("application/json"));
	Request->SetVerb("GET");

	return Request;
}

void AGaimer::RequestStartGame(FString name)
{
	FString init_game = "init_game?";
	init_game = init_game + FString("name=") + name;

	TSharedRef<IHttpRequest> Request = CreateRequest(init_game);

	Request->OnProcessRequestComplete().BindUObject(this, &AGaimer::OnGameStarted);
	Request->ProcessRequest();
}

void AGaimer::ConsumePlay()
{
	if (mRemainingPlays == 0)
		return;

	FString update_play = "consume_play?";
	update_play = update_play + FString("playid=") + FString::FromInt(mGameBeingWatched.num_plays - mRemainingPlays);

	TSharedRef<IHttpRequest> Request = CreateRequest(update_play);

	Request->OnProcessRequestComplete().BindUObject(this, &AGaimer::OnPlayConsumed);
	Request->ProcessRequest();
}

void AGaimer::ResetGame()
{
	if (mGameBegun)
	{
		mRemainingPlays = mGameBeingWatched.num_plays;
		mEndGame = false;
	}
	else
	{
		mRemainingPlays = 0;
	}
}

void AGaimer::EndGame()
{
	mEndGame = true;
	mGameBegun = false;
	mGameBeingWatched = FGameDetails();
}


// Called every frame
void AGaimer::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

	if (!mGameBegun)
	{
		return;
	}
}

// Called to bind functionality to input
void AGaimer::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
	Super::SetupPlayerInputComponent(PlayerInputComponent);

	PlayerInputComponent->BindAction(TEXT("Consume"), EInputEvent::IE_Pressed, this, &AGaimer::ConsumePlay);

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

void AGaimer::OnGameStarted(FHttpRequestPtr Request, FHttpResponsePtr Response, bool bWasSuccessful)
{
	if (!IsResponseGood(Response, bWasSuccessful))
	{
		return;
	}

	GetStructFromJsonString<FGameDetails>(Response, mGameBeingWatched);
	mGameBegun = true;
	ResetGame();
	

	UE_LOG(LogTemp, Warning, TEXT("Game begun with %d plays"), mGameBeingWatched.num_plays);
}

void AGaimer::OnPlayConsumed(FHttpRequestPtr Request, FHttpResponsePtr Response, bool bWasSuccessful)
{
	if (!IsResponseGood(Response, bWasSuccessful))
	{
		return;
	}

	FPlayReaction playReaction;
	GetStructFromJsonString<FPlayReaction>(Response, playReaction);

	UE_LOG(LogTemp, Warning, TEXT("Need emotion: %d for play %d"), playReaction.emotion_label, (mGameBeingWatched.num_plays - mRemainingPlays));

	mRemainingPlays--;
	if (mRemainingPlays == 0)
	{
		EndGame();
	}

	mCurrentReaction = playReaction;
}

template <typename StructType>
void AGaimer::GetJsonStringFromStruct(StructType FilledStruct, FString& StringOutput) 
{
	FJsonObjectConverter::UStructToJsonObjectString(StructType::StaticStruct(), &FilledStruct, StringOutput, 0, 0);
}

template <typename StructType>
void AGaimer::GetStructFromJsonString(FHttpResponsePtr Response, StructType& StructOutput) 
{
	FString JsonString = Response->GetContentAsString();
	JsonString.ReplaceInline(TEXT("\'"), TEXT("\""));
	FJsonObjectConverter::JsonObjectStringToUStruct<StructType>(JsonString, &StructOutput, 0, 0);
}